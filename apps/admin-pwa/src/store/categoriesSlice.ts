import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import type { CategoryNode, CategoryPayload } from "../lib/api";
import { createCategory, deleteCategory, fetchCategories, updateCategory } from "../lib/api";
import type { RootState } from ".";

interface CategoriesState {
  tree: CategoryNode[];
  loading: boolean;
  error: string | null;
}

const initialState: CategoriesState = {
  tree: [],
  loading: false,
  error: null
};

const selectToken = (state: RootState) => state.auth.accessToken ?? "";

export const loadCategories = createAsyncThunk<CategoryNode[], void, { state: RootState }>(
  "categories/load",
  async (_payload, thunkAPI) => {
    const token = selectToken(thunkAPI.getState());
    return fetchCategories(token);
  }
);

export const addCategory = createAsyncThunk<CategoryNode, CategoryPayload, { state: RootState }>(
  "categories/create",
  async (payload, thunkAPI) => {
    const token = selectToken(thunkAPI.getState());
    return createCategory(token, payload);
  }
);

export const patchCategory = createAsyncThunk<
  CategoryNode,
  { id: number; data: Partial<CategoryPayload> },
  { state: RootState }
>("categories/update", async ({ id, data }, thunkAPI) => {
  const token = selectToken(thunkAPI.getState());
  return updateCategory(token, id, data);
});

export const removeCategory = createAsyncThunk<number, number, { state: RootState }>(
  "categories/delete",
  async (id, thunkAPI) => {
    const token = selectToken(thunkAPI.getState());
    await deleteCategory(token, id);
    return id;
  }
);

function upsertNode(tree: CategoryNode[], node: CategoryNode): CategoryNode[] {
  let handled = false;

  const walk = (nodes: CategoryNode[]): CategoryNode[] =>
    nodes.map((item) => {
      if (item.id === node.id) {
        handled = true;
        return { ...node };
      }

      let children: CategoryNode[] | undefined = item.children;
      if (!handled && node.parent === item.id) {
        handled = true;
        children = [...(children ?? []), { ...node }];
      } else if (children && children.length) {
        children = walk(children);
      }

      return { ...item, children };
    });

  const result = walk(tree);
  if (!handled && node.parent == null) {
    return [...result, { ...node }];
  }

  return result;
}

function removeNode(tree: CategoryNode[], id: number): CategoryNode[] {
  return tree
    .filter((node) => node.id !== id)
    .map((node) => ({
      ...node,
      children: node.children ? removeNode(node.children, id) : node.children
    }));
}

const categoriesSlice = createSlice({
  name: "categories",
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(loadCategories.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loadCategories.fulfilled, (state, action) => {
        state.loading = false;
        state.tree = action.payload;
      })
      .addCase(loadCategories.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? "Не удалось загрузить категории";
      })
      .addCase(addCategory.fulfilled, (state, action) => {
        state.tree = upsertNode(state.tree, action.payload);
      })
      .addCase(patchCategory.fulfilled, (state, action) => {
        state.tree = upsertNode(state.tree, action.payload);
      })
      .addCase(removeCategory.fulfilled, (state, action) => {
        state.tree = removeNode(state.tree, action.payload);
      });
  }
});

export default categoriesSlice.reducer;

